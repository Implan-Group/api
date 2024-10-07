using System.Net;
using System.Security.Authentication;
using ConsoleApp.Regions;
using RestSharp.Authenticators;
using RestSharp.Serializers.Json;

namespace ConsoleApp.Services;

/*
# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

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
            BaseUrl = new Uri("https://api.implan.com/"),

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
        // Set the bearer token
        _jwtAuthenticator.SetBearerToken(bearerToken);
        // Validate that we can hit a small endpoint
        try
        {
            RegionEndpoints.GetRegionTypes();
        }
        catch (Exception ex)
        {
            throw new AuthenticationException("Invalid Bearer Token", ex);
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
            Logging.LogRequestResponse(_restClient, request, response!, null, timer.Elapsed);
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
            Logging.LogRequestResponse(_restClient, request, response!, response.Data, timer.Elapsed, typeof(T));
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
        RestResponse response = GetResponse(request);
        return response.Content;
    }

    /// <summary>
    /// Sends a <see cref="RestRequest"/> and returns the deserialized <typeparamref name="T"/> Data of the <see cref="RestResponse{T}"/>
    /// </summary>
    /// <param name="request"></param>
    /// <typeparam name="T"></typeparam>
    /// <returns></returns>
    public static T? GetResponseData<T>(RestRequest request)
    {
        RestResponse<T> response = GetResponse<T>(request);
        // Response.Data is the deserialized value from the json response body
        return response.Data;
    }
}
