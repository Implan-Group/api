namespace ConsoleApp.Workflows;

public class AuthenticationWorkflow : IWorkflow
{
    public static void Examples()
    {
#if DEBUG
        Rest.SetAuthentication("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il95RlFIVmtRd1ptaU0yaWpXbVdZeSJ9.eyJzZXNzaW9uTGlmZXRpbWUiOjgsImlkbGVTZXNzaW9uTGlmZXRpbWUiOjgsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2VtYWlsYWRkcmVzcyI6InRpbW90aHkuamF5QGltcGxhbi5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9naXZlbm5hbWUiOiJUaW1vdGh5IiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc3VybmFtZSI6IkpheSIsImlzRXpQcm94eVVzZXIiOmZhbHNlLCJpc3MiOiJodHRwczovL2Rldi1sb2dpbi5pbXBsYW4uY29tLyIsInN1YiI6ImF1dGgwfDY0Yjk0M2U2ODY5YjdhMDk4ZDRmYmY1YiIsImF1ZCI6WyJodHRwczovL3NlcnZpY2VzLmltcGxhbi5jb20iLCJodHRwczovL2ltcGxhbi1kZXYudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTcxOTQxMzQ0MCwiZXhwIjoxNzE5NDQyMjQwLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiYXpwIjoiVlBQR0k5Q1FqdlRSNGlTNmVGdmxRaFNvTlJ2eDUyZ2IifQ.CP-kmaY--M3G5ttPTV3j2F_kfb1ulR3pUMGua6KaEF0LDbYGAD2ZlIYopG9t0HCyjL4KRQdsNB3DRG3FdOVR1P2SWNDzEoa7ew9IDNt9IrxiviTsD_zp7Ls8PJrwt76o5H89NiUmBtWmtYOFPZkP0MY-24JgHnEifHV57sQD5w1w7bVh3QhNprwdewCYfQg-DpVAzb1UFJu14NOD9YVxCVf21QrKpL8o69FByqd7jIkYpfCREy-egJOyR8dV-xZuVqp-sVvsIYcKd3_WdbaoAMJlEumnpjxI2wGMds0GhBKxDO5WpN5Ab1g0B0MrBPbE6Vy2tQIVEt1KS_JmxChxyQ");
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