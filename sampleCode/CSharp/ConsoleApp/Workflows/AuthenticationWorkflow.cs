namespace ConsoleApp.Workflows;

public class AuthenticationWorkflow : IWorkflow
{
    public static void Examples()
    {
#if DEBUG
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

        // Retreive the token
        var bearerToken = Authentication.GetBearerToken(auth);

        // Set it so that RestSharp automatically includes it with all requests
        Rest.SetAuthentication(bearerToken);
    }
}