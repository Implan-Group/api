﻿using System.Security.Authentication;

namespace ConsoleApp.Endpoints;

public sealed record class ImplanAuthentication
{
    public string Username { get; set; }
    public string Password { get; set; }
}

public static class Authentication
{
    //TODO: Try setting the auth timeout in Gateway higher? (1min?)
    
    public static string GetBearerToken(ImplanAuthentication auth)
    {
        // The /auth endpoint handles authentication for all of ImpactApi
        var authRequest = new RestRequest("/auth");
        authRequest.Method = Method.Post;
        // The username + password must be passed in via Json body
        authRequest.AddJsonBody(auth);

        // Authentication must succeed and return a valid Bearer Token for any other ImpactApi calls to work
        var response = Rest._restClient.ExecutePost(authRequest);
        if (!response.IsSuccessStatusCode)
        {
            throw new AuthenticationException("Cannot currently Authenticate to Impact Api");
            // TODO: Wait + Retry Loop
        }

        // The response from this endpoint is a JWT Bearer token string "Bearer XXX...XXX"
        var token = response.Content;
        if (token.IsNullOrWhiteSpace())
            throw new AuthenticationException("Cannot currently Authenticate to Impact Api");

        return token;
    }
}