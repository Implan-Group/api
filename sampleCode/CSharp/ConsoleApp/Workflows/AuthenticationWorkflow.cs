namespace ConsoleApp.Workflows;

public class AuthenticationWorkflow : IWorkflow
{
    public static void Execute()
    {
#if DEBUG
        Rest.SetAuthentication(
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il95RlFIVmtRd1ptaU0yaWpXbVdZeSJ9.eyJzZXNzaW9uTGlmZXRpbWUiOjgsImlkbGVTZXNzaW9uTGlmZXRpbWUiOjgsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2VtYWlsYWRkcmVzcyI6InRpbW90aHkuamF5QGltcGxhbi5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9naXZlbm5hbWUiOiJUaW1vdGh5IiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc3VybmFtZSI6IkpheSIsImlzRXpQcm94eVVzZXIiOmZhbHNlLCJpc3MiOiJodHRwczovL2Rldi1sb2dpbi5pbXBsYW4uY29tLyIsInN1YiI6ImF1dGgwfDY0Yjk0M2U2ODY5YjdhMDk4ZDRmYmY1YiIsImF1ZCI6WyJodHRwczovL3NlcnZpY2VzLmltcGxhbi5jb20iLCJodHRwczovL2ltcGxhbi1kZXYudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTcxNzUwNjkxNiwiZXhwIjoxNzE3NTM1NzE2LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXpwIjoiVlBQR0k5Q1FqdlRSNGlTNmVGdmxRaFNvTlJ2eDUyZ2IifQ.CC1lW_tEQ0jEkbWGvWIyVacSHIrdMaCKcenbHFQmgMjQZ2eR96Jt5UZ-x4XeVfkGyT2efANXN207iC2DFGsMhYPuNC-T7tLMUWXns48X9SiyekeKnkBwKLAY3wOUjd--UcQVUqikabd7v9wHfyAhWN2QSAtNE4O22XACjOJzR4tL2aMG6Kl4dIQxtm9shSK9o2pW0ujFeOQUdMa3qul9FhjuwyHQBpaZIm-QKnPKWA_7DW53WfKVz7hdchCBjhHwZlz4Vv_v5EK8MOeEW8Lylpgry-l4Tf9vY6WapIRCQiUP7x24ASczZbZJjSOCPVliGf_6X1622W1f7jLqi3TYkQ");
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