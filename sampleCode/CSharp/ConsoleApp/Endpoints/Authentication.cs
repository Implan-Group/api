using System.Security.Authentication;

namespace ConsoleApp.Endpoints;

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

public sealed record class ImplanAuthentication
{
    public string Username { get; set; }
    public string Password { get; set; }
}

public static class Authentication
{
    /// <summary>
    /// Retrieves a JWT Bearer Token from the Auth endpoint for the user with the given credentials
    /// </summary>
    public static string GetBearerToken(ImplanAuthentication auth)
    {
        // The /auth endpoint handles authentication for all of ImpactApi
        RestRequest authRequest = new RestRequest("/auth");
        authRequest.Method = Method.Post;
        // The username + password must be passed in via Json body
        authRequest.AddJsonBody(auth);

        // Authentication must succeed and return a valid Bearer Token for any other ImpactApi calls to work
        RestResponse response = Rest._restClient.ExecutePost(authRequest);
        if (!response.IsSuccessStatusCode)
        {
            throw new AuthenticationException("Cannot currently Authenticate to Impact Api");
            // TODO: Wait + Retry Loop?
        }

        // The response from this endpoint is a JWT Bearer token string "Bearer XXX...XXX"
        string? token = response.Content;
        if (token.IsNullOrWhiteSpace())
            throw new AuthenticationException("Cannot currently Authenticate to Impact Api");

        return token;
    }
}
