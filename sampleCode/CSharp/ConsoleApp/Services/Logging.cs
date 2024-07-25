namespace ConsoleApp.Services;

/// <summary>
/// All the code that logs details to the <see cref="Console"/>
/// </summary>
public static class Logging
{
    // shared instance
    private static readonly StringBuilder _stringBuilder = new();
    // the path to the log file
    private static readonly string _logFilePath;

    static Logging()
    {
        // Ensure that the Console can display all UTF8 characters
        Console.OutputEncoding = Encoding.UTF8;

        // Start with the directory we're executing from
        var dir = AppDomain.CurrentDomain.BaseDirectory;
        // We want to be in the same root as the /bin/ directory
        var binIndex = dir.IndexOf(@"\bin", StringComparison.OrdinalIgnoreCase);
        if (binIndex >= 0)
            dir = dir.Substring(0, binIndex);
        var logDir = Path.Combine(dir, "logs");
        
        // Ensure that directory exists so that we can write log files to it
        Directory.CreateDirectory(logDir);

        // Log file uses the day's timestamp
        var fileName = $"Log_{DateTime.Now:yyyyMMdd}.txt";
        _logFilePath = Path.Combine(logDir, fileName);
    }

    /// <summary>
    /// Logs a <see cref="RestRequest"/> + <see cref="RestResponse"/> to the Console
    /// </summary>
    internal static void LogRequestResponse(
        RestClient client,
        RestRequest request,
        RestResponse response,
        object? responseData,
        TimeSpan elapsedTime,
        Type? responseDataType = null)
    {
        StringBuilder log = _stringBuilder.Clear();

        // Timestamp header
        log.AppendLine("-------------")
            .AppendLine($"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}]");

        // Request
        string method = request.Method.ToString().ToUpper();
        log.AppendLine($"Request: {method} '{client.BuildUri(request)}'");
        foreach (Parameter param in request.Parameters)
        {
            // These parameter types will be resolved as part of BuildUri
            if (param is UrlSegmentParameter or GetOrPostParameter) continue;

            // Skip logging common parameters
            if (param.Name == "Authorization") continue;

            // Json = Body!
            if (param is JsonParameter jsonParameter)
            {
                log.AppendLine($"-Body: '{jsonParameter.ContentType}' from {jsonParameter.Value?.GetType().Name}");
                // Prettify the json
                string json = Json.Serialize(jsonParameter.Value);
                log.AppendLine(json);
                continue;
            }

            // Header?
            if (param is HeaderParameter headerParameter)
            {
                log.AppendLine($"-H {headerParameter.Name} {headerParameter.Value}");
                continue;
            }

            // Unknown Parameter, skip it
            continue;
        }

        // Response
        log.AppendLine(
            $"Response: '{(int)response.StatusCode} {response.StatusCode}' in {elapsedTime.TotalMilliseconds:N1}ms");

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
                string message = response.ErrorException.Message;
                // Push long messages to the next line
                if (message.Length > 80)
                {
                    log.AppendLine()
                        .Append(' ');
                }

                log.AppendLine($"'{message}'");
            }
        }
        
        // We want to log the content for debugging + verification
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
            
            if (responseData is not null)
            {
                // prettify the json
                string json = Json.Serialize(responseData);
                log.AppendLine(json);
            }
            else
            {
                string? content = response.Content;
                log.AppendLine(content);
            }
        }
        
        // Final empty line
        log.AppendLine();

        string logMessage = log.ToString();

        // Write the final log to the Console
        Console.WriteLine(logMessage);

        // Append to the log file
        File.AppendAllText(_logFilePath, logMessage, Encoding.UTF8);
    }
}