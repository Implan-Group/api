namespace ConsoleApp.Workflows;

public class AuthenticationWorkflow : IWorkflow
{
    public static void Examples()
    {
#if DEBUG
        Rest.SetAuthentication("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il95RlFIVmtRd1ptaU0yaWpXbVdZeSJ9.eyJzZXNzaW9uTGlmZXRpbWUiOjgsImlkbGVTZXNzaW9uTGlmZXRpbWUiOjgsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2VtYWlsYWRkcmVzcyI6InRpbW90aHkuamF5QGltcGxhbi5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9naXZlbm5hbWUiOiJUaW1vdGh5IiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc3VybmFtZSI6IkpheSIsImlzRXpQcm94eVVzZXIiOmZhbHNlLCJpc3MiOiJodHRwczovL2Rldi1sb2dpbi5pbXBsYW4uY29tLyIsInN1YiI6ImF1dGgwfDY0Yjk0M2U2ODY5YjdhMDk4ZDRmYmY1YiIsImF1ZCI6WyJodHRwczovL3NlcnZpY2VzLmltcGxhbi5jb20iLCJodHRwczovL2ltcGxhbi1kZXYudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTcxOTQ5OTEwMywiZXhwIjoxNzE5NTI3OTAzLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXpwIjoiVlBQR0k5Q1FqdlRSNGlTNmVGdmxRaFNvTlJ2eDUyZ2IifQ.m2AdQC1KAiUh39fzr5frzDLtzgo5vW6XLXTOEL8GpbvS_o64Wqhc4ufP53Zwske69V2MGQj6x-Ob6BvXkVft35c8qy6kfbCkb0MHQbfuQIwnQVi1sn7fdgWcI6nRCvH5qcUuTXhSWL0s0KUeen8B7bLmYO6pW9V65Shd3gkg7P3mq8xNMKaGKVQTzjCR30A4goKKCnmCoJp8sOCQWcFj6UDIDIFy3XKpWw_befHXqYkDwXdiRvTbegmW2O2HptFYrVufYEd0neSiBq17TpH4MRgi2Agzw-xrrTVFrgaC9zcZaxzDzC2gY_UvSQpYzAHSr9MlXZt1T5Uk_mWZHZM0tw");
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