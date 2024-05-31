using System.Security.Authentication;
using RestSharp.Authenticators;
using RestSharp.Serializers.Json;

namespace ConsoleApp.Services;

public static class Rest
{
    private static readonly RestClientOptions _restClientOptions;
    private static readonly RestClient _restClient;
    private static readonly JwtAuthenticator _jwtAuthenticator;
    private static ImplanAuthentication? _implanAuthentication;

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
        ArgumentException.ThrowIfNullOrWhiteSpace(username);
        ArgumentException.ThrowIfNullOrWhiteSpace(password);
        
        _implanAuthentication = new ImplanAuthentication()
        {
            Username = username,
            Password = password,
        };
        Authenticate(); // verify immediately
    }

    public static void SetAuthentication(string bearerToken)
    {
        _jwtAuthenticator.SetBearerToken(bearerToken);
        // Validate that we can hit a small endpoint
        try
        {
            Regions.GetRegionTypes();
        }
        catch (Exception ex)
        {
            throw new AuthenticationException("Invalid Bearer Token");
        }
    }

    /// <summary>
    /// Authenticate to Implan API and store the JWT Bearer Token for subsequent re-use
    /// </summary>
    /// <exception cref="AuthenticationException"></exception>
    private static void Authenticate()
    {
        if (_implanAuthentication is null)
        {
            throw new AuthenticationException(
                $"You must call {nameof(Rest)}.{nameof(SetAuthentication)}() before using {nameof(Rest)}");
        }

        // The /auth endpoint handles authentication for all of ImpactApi
        var authRequest = new RestRequest("/auth");
        authRequest.Method = Method.Post;
        // The username + password must be passed in via Json body
        authRequest.AddJsonBody(_implanAuthentication);

        // Authentication must succeed and return a valid Bearer Token for any other ImpactApi calls to work
        var response = _restClient.ExecutePost(authRequest);
        if (!response.IsSuccessStatusCode)
        {
            // This is a service timeout
            throw new AuthenticationException("Cannot currently Authenticate to Impact Api");
            
            // TODO: Wait + Retry Loop
        }
        
        // The response from this endpoint is a JWT Bearer token string "Bearer XXX...XXX"
        var token = response.Content;
        if (token.IsNullOrWhiteSpace())
            throw new AuthenticationException("Cannot currently Authenticate to Impact Api");

        // Store the JWT Bearer Token for all future requests
        _jwtAuthenticator.SetBearerToken(token);
    }
    
    public static RestResponse GetResponse(RestRequest request)
    {
        RestResponse? response = null;
        Stopwatch timer = new Stopwatch();
        try
        {
            timer.Start();
            response = _restClient.Execute(request, request.Method);
        }
        catch (Exception ex)
        {
            response ??= new RestResponse();
            response.ErrorException = ex;
        }
        finally
        {
            timer.Stop();
            Logging.LogRequestResponse(_restClient, request, response!, timer.Elapsed);
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
        }
        catch (Exception ex)
        {
            response ??= new RestResponse<T>(request);
            response.ErrorException = ex;
        }
        finally
        {
            timer.Stop();
            Logging.LogRequestResponse(_restClient, request, response!, timer.Elapsed, typeof(T));
        }

        return response;
    }

    /// <summary>
    /// Sends a <see cref="RestRequest"/> and returns the <see cref="string"/> Content of the <see cref="RestResponse"/>
    /// </summary>
    /// <param name="request"></param>
    /// <returns></returns>
    public static string GetResponseContent(RestRequest request)
    {
        var response = GetResponse(request);
        return response.Content.ThrowIfNull();
    }

    /// <summary>
    /// Sends a <see cref="RestRequest"/> and returns the deserialized <typeparamref name="T"/> Data of the <see cref="RestResponse{T}"/>
    /// </summary>
    /// <param name="request"></param>
    /// <typeparam name="T"></typeparam>
    /// <returns></returns>
    public static T? GetResponseData<T>(RestRequest request)
    {
        var response = GetResponse<T>(request);
        // Response.Data is the deserialized value from the json response body
        return response.Data;//.ThrowIfNull();
    }
}