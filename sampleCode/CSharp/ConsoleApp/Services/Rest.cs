using System.Diagnostics;
using System.Net;
using System.Security.Authentication;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using ConsoleApp.Models;
using RestSharp;
using RestSharp.Authenticators;
using RestSharp.Serializers.Json;

namespace ConsoleApp.Services;

public static class Rest
{
    private static readonly RestClientOptions _restClientOptions;
    private static readonly RestClient _restClient;
    private static readonly JwtAuthenticator _jwtAuthenticator;
    private static ImplanAuthentication? _implanAuthentication = null;

    static Rest()
    {
        // start with a bad token that will be overwritten by ReAuthenticate
        _jwtAuthenticator = new JwtAuthenticator("BAD_TOKEN");
        _restClientOptions = new RestClientOptions
        {
            // This is the base endpoint for all Implan ImpactAPI Requests
            BaseUrl = new Uri("https://api.implan.com/int/"),

            // We use JWT Bearer Tokens (https://jwt.io/) that must be passed with every Request
            Authenticator = _jwtAuthenticator,

            ThrowOnDeserializationError = false,
            Timeout = TimeSpan.FromMinutes(1),
        };
        _restClient = new RestClient(_restClientOptions,
            configureSerialization: s => s.UseSystemTextJson(Json.JsonSerializerOptions));
    }

    /// <summary>
    /// Sets the authentication credentials used for all REST Requests
    /// </summary>
    /// <param name="username">The username of the Implan User</param>
    /// <param name="password">The password of the Implan User</param>
    /// <exception cref="AuthenticationException">
    /// Thrown if the <paramref name="username"/> or <paramref name="password"/> is invalid
    /// </exception>
    public static void SetAuthentication(string username, string password)
    {
        _implanAuthentication = new ImplanAuthentication()
        {
            Username = username,
            Password = password,
        };
        ReAuthenticate(); // verify immediately
    }

    private static void ReAuthenticate()
    {
        if (_implanAuthentication is null)
            throw new AuthenticationException(
                $"You must call {nameof(Rest)}.{nameof(SetAuthentication)}() before using {nameof(Rest)}");

        // There is a universal /auth endpoint for all authentication
        var authRequest = new RestRequest("/auth");
        // The username + password must be passed in via Json
        authRequest.AddJsonBody(_implanAuthentication);

        // Authentication must succeed to access any other endpoints
        var response = _restClient.ExecutePost(authRequest);
        if (!response.IsSuccessStatusCode || string.IsNullOrWhiteSpace(response.Content))
        {
            LogIfError(response);
            throw new AuthenticationException("Cannot Authenticate to Impact Api");
        }
        // The response from this endpoint is a string like "Bearer XXX...XXX"

        // Store the JWT Bearer Token for all future requests
        _jwtAuthenticator.SetBearerToken(response.Content);
    }

    private static void LogIfError(RestResponse response)
    {
        if (response.IsSuccessStatusCode &&
            response.ErrorException is null &&
            string.IsNullOrWhiteSpace(response.ErrorMessage))
        {
            return; // no issue here
        }

        var log = new StringBuilder();
        log.AppendLine($"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}]: Rest Response Failed")
            .AppendLine($"StatusCode: {response.StatusCode}");
        if (!string.IsNullOrWhiteSpace(response.ErrorMessage))
            log.AppendLine($"ErrorMessage: {response.ErrorMessage}");
        if (response.ErrorException is not null)
            log.AppendLine($"ErrorException: {response.ErrorException}");

        // Try to get the response as an Error
        ActionResult? error = Json.Deserialize<ActionResult>(response.Content);
        if (error is not null && !string.IsNullOrWhiteSpace(error.Type))
        {
            log.AppendLine(error.ToString());
        }

        // Try to get the response as a Message
        ErrorMessage? errorMessage = Json.Deserialize<ErrorMessage>(response.Content);
        if (errorMessage is not null && !string.IsNullOrWhiteSpace(errorMessage.Message))
        {
            log.AppendLine(errorMessage.Message);
        }

        Debug.WriteLine(log.ToString());
    }

    private static string GetLogJson(RestRequest request)
    {
        var loggable = new
        {
            resource = request.Resource,
            // Parameters are custom anonymous objects in order to have the parameter type as a nice string
            // otherwise it will just show the enum value
            parameters = request.Parameters.Select(parameter => new
            {
                name = parameter.Name,
                value = parameter.Value,
                type = parameter.Type.ToString()
            }),
            // ToString() here to have the method as a nice string otherwise it will just show the enum value
            method = request.Method.ToString(),
            // This will generate the actual Uri used in the request
            uri = _restClient.BuildUri(request),
        };
        string json = Json.Serialize(loggable);
        return json;
    }

    private static string GetLogJson(RestResponse? response)
    {
        if (response is null) return "null";
        var loggable = new
        {
            statusCode = response.StatusCode,
            content = response.Content,
            headers = response.Headers,
            // The Uri that actually responded (could be different from the requestUri if a redirection occurred)
            responseUri = response.ResponseUri,
            errorMessage = response.ErrorMessage,
        };
        string json = Json.Serialize(loggable);
        return json;
    }

    public static RestResponse GetResponse(RestRequest request)
    {
        RestResponse? response = null;
        Stopwatch timer = new Stopwatch();
        try
        {
            timer.Start();
            response = _restClient.Execute(request, request.Method);
            timer.Stop();

            LogIfError(response);
            
            Debug.WriteLine(
                $"""
                 [{DateTime.Now:yyyy-MM-dd HH:mm:ss}]: Rest Request completed in {timer.Elapsed:g}
                 Request:
                 {GetLogJson(request)}
                 Response:
                 {GetLogJson(response)}
                 """);
        }
        catch (Exception ex)
        {
            timer.Stop();
            Debug.WriteLine(
                $"""
                 [{DateTime.Now:yyyy-MM-dd HH:mm:ss}]: Rest Request failed in {timer.Elapsed:g}
                 Request:
                 {GetLogJson(request)}
                 Response:
                 {GetLogJson(response)}
                 Exception:
                 {ex.GetType()} {ex.Message}
                 {ex.StackTrace}
                 """);
            throw;
        }

        return response;
    }

    public static RestResponse<T> GetResponse<T>(RestRequest request)
    {
        RestResponse<T>? response = null;
        Stopwatch timer = new Stopwatch();
        try
        {
            timer.Start();
            response = _restClient.Execute<T>(request, request.Method);
            timer.Stop();

            LogIfError(response);

            if (response.StatusCode == HttpStatusCode.Unauthorized)
            {
                Debug.WriteLine(
                    $"""
                     [{DateTime.Now:yyyy-MM-dd HH:mm:ss}]: Rest Request completed in {timer.Elapsed:g}
                     Request:
                     {GetLogJson(request)}
                     Response:
                     {GetLogJson(response)}
                     """);
            }

            Debug.WriteLine(
                $"""
                 [{DateTime.Now:yyyy-MM-dd HH:mm:ss}]: Rest Request completed in {timer.Elapsed:g}
                 Request:
                 {GetLogJson(request)}
                 Response:
                 {GetLogJson(response)}
                 """);
        }
        catch (Exception ex)
        {
            timer.Stop();
            Debug.WriteLine(
                $"""
                 [{DateTime.Now:yyyy-MM-dd HH:mm:ss}]: Rest Request failed in {timer.Elapsed:g}
                 Request:
                 {GetLogJson(request)}
                 Response:
                 {GetLogJson(response)}
                 Exception:
                 {ex.GetType()} {ex.Message}
                 {ex.StackTrace}
                 """);
            throw;
        }

        return response;
    }

    public static string GetResponseContent(RestRequest request)
    {
        var response = GetResponse(request);
        return response.Content.ThrowIfNull();
    }

    public static T? GetResponseData<T>(RestRequest request)
    {
        var response = GetResponse<T>(request);
        // Response.Data is the deserialized value from the json response body
        return response.Data;//.ThrowIfNull();
    }
}