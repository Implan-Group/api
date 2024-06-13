using System.Net;
using System.Security.Authentication;
using RestSharp.Authenticators;
using RestSharp.Serializers.Json;

namespace ConsoleApp.Services;

/// <summary>
/// Contains all the boilerplate to send Rest Requests, handle errors, log, and return Responses
/// </summary>
public static class Rest
{
    private static readonly RestClientOptions _restClientOptions;
    internal static readonly RestClient _restClient;
    private static readonly JwtAuthenticator _jwtAuthenticator;
    private static ImplanAuthentication? _implanAuthentication;

    static Rest()
    {
        // start with a placeholder token (to be overriden with SetAuthentication)
        _jwtAuthenticator = new JwtAuthenticator("BAD_TOKEN");
        // setup the defaults for all Rest requests
        _restClientOptions = new RestClientOptions
        {
            // This is the base endpoint for all Implan ImpactAPI Requests
#if DEBUG
            // TODO: Remove these testing URLs
            BaseUrl = new Uri("https://api.implan.com/int/"),           // Running against External INT
            //BaseUrl = new Uri("https://localhost:5001/external/"),    // Running against Local INT
#else
            BaseUrl = new Uri("https://api.implan.com/"),
#endif

            AutomaticDecompression = DecompressionMethods.All,

            // We use JWT Bearer Tokens (https://jwt.io/) that must be passed with every Request
            Authenticator = _jwtAuthenticator,

            ThrowOnDeserializationError = false,
            Timeout = TimeSpan.FromMinutes(1),
        };
        // Configure RestSharp to use System.Text.Json for serialization/deserialization
        _restClient = new RestClient(_restClientOptions,
            configureSerialization: s => s.UseSystemTextJson(Json.JsonSerializerOptions));
    }

    private static void ThrowOnError(RestResponse response)
    {
        if (response.IsSuccessStatusCode &&
            response.ErrorException is null &&
            response.ErrorMessage is null) return;

        Exception ex = response.ErrorException ?? new InvalidOperationException("Rest Request Failed");
        throw ex;
    }

    public static void SetAuthentication(string bearerToken)
    {
        _jwtAuthenticator.SetBearerToken(bearerToken);
        // Validate that we can hit a small endpoint
        try
        {
#if !DEBUG
            Regions.GetRegionTypes();
#endif
        }
        catch (Exception ex)
        {
            throw new AuthenticationException("Invalid Bearer Token");
        }
    }

    public static RestResponse GetResponse(RestRequest request)
    {
        RestResponse? response = null;
        Stopwatch timer = new Stopwatch();
        try
        {
            timer.Start();
            response = _restClient.Execute(request, request.Method);
            //ThrowOnError(response);
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
            //ThrowOnError(response);
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
    public static string? GetResponseContent(RestRequest request)
    {
        var response = GetResponse(request);
        return response.Content; //.ThrowIfNull();
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
        return response.Data; //.ThrowIfNull();
    }
}