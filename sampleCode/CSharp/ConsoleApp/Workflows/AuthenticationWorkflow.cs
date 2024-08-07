﻿namespace ConsoleApp.Workflows;

public class AuthenticationWorkflow : IWorkflow
{
    public static void Examples()
    {
#if DEBUG
        // During debugging, it may be helpful to just pass the Bearer Token directly, rather than having to authenticate
        // every single time the application is run
        
        Rest.SetAuthentication("");
        return;
#endif

        /* The very first step to accessing Implan's ImpactApi is to authenticate to the service.
           Your current Implan Username + Password needs to be sent to the authentication service in order to retrieve a
           JWT Bearer Token (https://jwt.io/)
           This bearer token must be included as a header in every single other request to ImpactApi.
           `Authorization: Bearer <token>`
         */

        ImplanAuthentication auth = new ImplanAuthentication()
        {
            Username = "",
            Password = "",
        };

        // Retrieve the token
        string bearerToken = Authentication.GetBearerToken(auth);

        // Set it so that RestSharp automatically includes it with all requests
        Rest.SetAuthentication(bearerToken);
    }
}