﻿#if DEBUG
#define VERBOSE
#endif

namespace ConsoleApp.Services;

/// <summary>
/// All the code that logs details to the <see cref="Console"/>
/// </summary>
public static class Logging
{
    // shared instance
    private static readonly StringBuilder _stringBuilder = new();

    static Logging()
    {
        // Ensure that the Console can display all UTF8 characters
        Console.OutputEncoding = Encoding.UTF8;
    }

    /// <summary>
    /// Logs a <see cref="RestRequest"/> + <see cref="RestResponse{T}"/> to the Console
    /// </summary>
    /// <param name="client"></param>
    /// <param name="request"></param>
    /// <param name="response"></param>
    /// <param name="elapsedTime"></param>
    /// <param name="responseDataType"></param>
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
#if VERBOSE
                log.AppendLine($" '{json}'");
#else
                if (json.Length <= 80)
                {
                    log.AppendLine($" '{json}'");
                }
                else
                {
                    log.AppendLine($" '{json.AsSpan(..80)}…'");
                }
#endif
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
                var message = response.ErrorException.Message;
                // Push long messages to the next line
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
#if VERBOSE
            log.AppendLine($" '{content}'");
#else
            if (content.Length <= 80)
            {
                log.AppendLine($" '{content}'");
            }
            else
            {
                // Clip overly-long messages
                log.AppendLine($" '{content.AsSpan(..80)}…'");
            }
#endif
        }

        string logMessage = log.ToString();

        // Write the final log to the Console
        Console.WriteLine(logMessage);
    }
}