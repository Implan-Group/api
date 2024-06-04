using System.Net;
using System.Security.Authentication;
using RestSharp.Authenticators;
using RestSharp.Serializers.Json;

namespace ConsoleApp.Services;

public static class Rest
{
    private static readonly RestClientOptions _restClientOptions;
    internal static readonly RestClient _restClient;
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
            //BaseUrl = new Uri("https://localhost:5001/external/"),

            AutomaticDecompression = DecompressionMethods.All,

            // We use JWT Bearer Tokens (https://jwt.io/) that must be passed with every Request
            Authenticator = _jwtAuthenticator,

            ThrowOnDeserializationError = false,
            Timeout = TimeSpan.FromMinutes(1),
        };
        _restClient = new RestClient(_restClientOptions,
            configureSerialization: s => s.UseSystemTextJson(Json.JsonSerializerOptions));
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