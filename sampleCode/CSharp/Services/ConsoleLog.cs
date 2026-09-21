using System.Text;

namespace Implan.ApiSamples.Services;

/// <summary>
/// Console and file logging for the samples.
/// </summary>
/// <remarks>
/// Two audiences. The console gets a readable narration of what a workflow is
/// doing. The log file gets the full request and response detail, which is what you
/// send to support@implan.com when something is wrong.
///
/// The <c>Authorization</c> header is redacted in both. A bearer token is a
/// credential: it is as good as your password for the next 24 hours, so it never
/// reaches a console, a log file, or a screenshot.
/// </remarks>
public static class ConsoleLog
{
    private static readonly Lock FileLock = new();
    private static string? _logFilePath;

    /// <summary>Header names never written out, compared case-insensitively.</summary>
    private static readonly HashSet<string> RedactedHeaders = new(StringComparer.OrdinalIgnoreCase)
    {
        "Authorization", "x-api-key", "Cookie", "Set-Cookie",
    };

    /// <summary>
    /// A response body longer than this is truncated in the log. Region and industry
    /// lists run to megabytes, and a log nobody can open helps nobody.
    /// </summary>
    private const int MaxLoggedBodyChars = 20_000;

    /// <summary>Today's log file. Created on first use.</summary>
    public static string LogFilePath
    {
        get
        {
            if (_logFilePath is not null)
                return _logFilePath;

            Directory.CreateDirectory(Config.LogDirectory);
            _logFilePath = Path.Combine(Config.LogDirectory, $"Log_{DateTime.Now:yyyyMMdd}.txt");
            return _logFilePath;
        }
    }

    /// <summary>Writes one line of narration to the console.</summary>
    public static void Info(string message = "")
    {
        Console.WriteLine(message);
    }

    /// <summary>Writes a formatted line of narration to the console.</summary>
    public static void Info(string format, params object?[] values)
    {
        Console.WriteLine(format, values);
    }

    /// <summary>
    /// Prints a step heading.
    /// </summary>
    /// <remarks>
    /// Workflows are written as numbered steps, and these are the headings. Keeping
    /// them in one place means every sample's console output looks the same.
    /// </remarks>
    public static void Heading(string text)
    {
        Console.WriteLine();
        Console.WriteLine(text);
        Console.WriteLine(new string('-', text.Length));
    }

    /// <summary>Appends a line to the log file only, not the console.</summary>
    public static void Debug(string message)
    {
        lock (FileLock)
        {
            File.AppendAllText(
                LogFilePath,
                $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} {message}{Environment.NewLine}",
                Encoding.UTF8);
        }
    }

    /// <summary>
    /// Writes one request and response pair to the log file.
    /// </summary>
    /// <remarks>
    /// This is the record to attach to a support ticket. It has the method, the full
    /// URL, the headers with credentials removed, both bodies, the status, and how
    /// long the call took.
    /// </remarks>
    public static void LogExchange(
        RestClient client,
        RestRequest request,
        RestResponse response,
        TimeSpan elapsed)
    {
        var log = new StringBuilder();
        log.AppendLine("--------");
        log.AppendLine($"{request.Method.ToString().ToUpperInvariant()} {client.BuildUri(request)}");

        foreach (var parameter in request.Parameters)
        {
            switch (parameter.Type)
            {
                case ParameterType.HttpHeader:
                    var name = parameter.Name ?? string.Empty;
                    var value = RedactedHeaders.Contains(name) ? "<redacted>" : parameter.Value?.ToString();
                    log.AppendLine($"  {name}: {value}");
                    break;

                case ParameterType.RequestBody:
                    log.AppendLine("  request body:");
                    log.AppendLine(Prettify(parameter.Value?.ToString()));
                    break;
            }
        }

        log.AppendLine(
            $"  -> {(int)response.StatusCode} {response.StatusCode} in {elapsed.TotalSeconds:F2}s");
        log.AppendLine($"  response content-type: {response.ContentType ?? "(none)"}");

        var body = Prettify(response.Content);
        if (body.Length > MaxLoggedBodyChars)
        {
            body = body[..MaxLoggedBodyChars]
                   + $"{Environment.NewLine}... truncated, {body.Length - MaxLoggedBodyChars} more characters";
        }

        if (!string.IsNullOrWhiteSpace(body))
        {
            log.AppendLine("  response body:");
            log.AppendLine(body);
        }

        Debug(log.ToString());
    }

    /// <summary>Renders a body for the log, prettified when it is JSON.</summary>
    private static string Prettify(string? body)
    {
        if (string.IsNullOrWhiteSpace(body))
            return string.Empty;

        var trimmed = body.TrimStart();
        if (!trimmed.StartsWith('{') && !trimmed.StartsWith('['))
            return body;

        try
        {
            using var document = JsonDocument.Parse(body);
            return JsonSerializer.Serialize(document, new JsonSerializerOptions { WriteIndented = true });
        }
        catch (JsonException)
        {
            // Not valid JSON after all; log it as it came.
            return body;
        }
    }
}
