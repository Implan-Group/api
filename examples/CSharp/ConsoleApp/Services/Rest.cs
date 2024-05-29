using System.Diagnostics;
using System.Net;
using System.Security.Authentication;
using System.Text.Json;
using System.Text.Json.Serialization;
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
            
            ThrowOnDeserializationError = true,
            Timeout = TimeSpan.FromMinutes(1),
        };
        _restClient = new RestClient(_restClientOptions,
            configureSerialization: s => s.UseSystemTextJson(Json._jsonSerializerOptions));
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
            throw new AuthenticationException($"You must call {nameof(Rest)}.{nameof(SetAuthentication)}() before using {nameof(Rest)}");
        
        // There is a universal /auth endpoint for all authentication
        var authRequest = new RestRequest("/auth");
        // The username + password must be passed in via Json
        authRequest.AddJsonBody(_implanAuthentication);
        
        // Authentication must succeed to access any other endpoints
        var response = _restClient.ExecutePost(authRequest);
        if (!response.IsSuccessStatusCode || string.IsNullOrWhiteSpace(response.Content))
        {
            throw new AuthenticationException("Cannot Authenticate to Impact Api");
        }
        // The response from this endpoint is a string like "Bearer XXX...XXX"
      
        // Store the JWT Bearer Token for all future requests
        _jwtAuthenticator.SetBearerToken(response.Content);
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

    private static RestResponse GetResponseImpl(RestRequest request)
    {
        RestResponse? response = null;
        Stopwatch timer = new Stopwatch();
        try
        {
            timer.Start();
            response = _restClient.Execute(request, request.Method);
            timer.Stop();
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
    private static RestResponse<T> GetResponseImpl<T>(RestRequest request)
    {
        RestResponse<T>? response = null;
        Stopwatch timer = new Stopwatch();
        try
        {
            timer.Start();
            response = _restClient.Execute<T>(request, request.Method);
            timer.Stop();
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

    
    private static TResponse Impl<TResponse>(Func<RestClient, TResponse> func)
        where TResponse : RestResponse
    {
        TResponse response;
        try
        {
            response = func(_restClient);
            // Auth fail we just reauthenticate
            if (response.StatusCode == HttpStatusCode.Unauthorized)
            {
                ReAuthenticate();
                // Try again (TODO: Fix infinite loop possibility)
                response = Impl<TResponse>(func);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex);
            throw;
        }

        if (response.IsSuccessStatusCode)
            return response;
        throw response.ErrorException ?? new InvalidOperationException("Could not execute RestRequest");
    }
    
    public static string? GetResponseContent(RestRequest request)
    {
        var uri = _restClient.BuildUri(request);

        try
        {
            return Impl(client => client.Execute(request, request.Method))
                .Content;
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex);
            throw;
        }
    }

    public static T GetResponseData<T>(RestRequest request)
    {
        var uri = _restClient.BuildUri(request);

        try
        {
            var data = Impl(client => client.Execute<T>(request, request.Method)).Data;
            if (data is null)
                throw new InvalidOperationException();
            return data;
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex);
            throw;
        }
    }
}