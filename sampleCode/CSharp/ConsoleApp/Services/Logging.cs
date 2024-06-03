namespace ConsoleApp.Services;

public static class Logging
{
    private static readonly StringBuilder _stringBuilder = new();
    
    static Logging()
    {
        Console.OutputEncoding = Encoding.UTF8;
    }

    internal static void LogRequestResponse(
        RestClient client,
        RestRequest request,
        RestResponse response,
        TimeSpan elapsedTime,
        Type? responseDataType = null)
    {
        var log = _stringBuilder.Clear();
        
        // Timestamp header
        log.AppendLine($"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}]");
        
        // Request
        string method = request.Method.ToString().ToUpper();
        log.AppendLine($"Request: {method} '{client.BuildUri(request)}'");
        foreach (var param in request.Parameters)
        {
            // These parameter types will be resolved as part of BuildUri
            if (param is UrlSegmentParameter or GetOrPostParameter) continue;
            
            // Skip logging common parameters
            if (param.Name == "Authorization") continue;

            // Json = Body!
            if (param is JsonParameter jsonParameter)
            {
                log.AppendLine($"-Body: '{jsonParameter.ContentType}' from {jsonParameter.Value?.GetType().Name}");
                string json = Json.Serialize(jsonParameter.Value);
                if (json.Length <= 80)
                {
                    log.AppendLine($" '{json}'");
                }
                else
                {
                    log.AppendLine($" '{json.AsSpan(..80)}…'");
                }
                continue;
            }
            
            // Header?
            if (param is HeaderParameter headerParameter)
            {
                log.AppendLine($"-H {headerParameter.Name} {headerParameter.Value}");
                continue;
            }
            
            Debugger.Break();
        }
        
        // Response
        log.AppendLine($"Response: '{(int)response.StatusCode} {response.StatusCode}' in {elapsedTime.TotalMilliseconds:N1}ms");
         
        // Failed?
        if (!response.IsSuccessStatusCode ||
            !response.ErrorMessage.IsNullOrWhiteSpace() ||
            response.ErrorException is not null)
        {
            if (!response.ErrorMessage.IsNullOrWhiteSpace())
            {
                log.AppendLine($"-Error Message: {response.ErrorMessage}");
            }

            if (response.ErrorException is not null)
            {
                log.Append($"-{response.ErrorException.GetType().Name}: ");
                var message = response.ErrorException.Message;
                if (message.Length > 80)
                {
                    log.AppendLine()
                        .Append(' ');
                }
                log.AppendLine($"'{message}'");
            }
        }
        
        if (!response.Content.IsNullOrWhiteSpace())
        {
            log.Append($"-Content: '{response.ContentType}'");
            if (responseDataType is not null)
            {
                log.AppendLine($" as {responseDataType.Name}");
            }
            else
            {
                log.AppendLine();
            }
            
            var content = response.Content;
            if (content.Length <= 80)
            {
                log.AppendLine($" '{content}'");
            }
            else
            {
                log.AppendLine($" '{content.AsSpan(..80)}…'");
            }
        }

        string logMessage = log.ToString();
        
        // Write
        Console.WriteLine(logMessage);
    }
}