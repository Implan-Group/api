using System.Diagnostics.CodeAnalysis;
using System.Runtime.CompilerServices;

namespace ConsoleApp.Services;

public static class Extensions
{
    [return: NotNull]
    public static T ThrowIfNull<T>(
        [AllowNull, NotNull] this T? value,
        [CallerArgumentExpression(nameof(value))]
        string? valueName = null)
    {
        if (value is not null)
            return value;
        throw new ArgumentNullException(valueName);
    }

    public static bool IsNullOrWhiteSpace([NotNullWhen(false)] this string? str)
    {
        return string.IsNullOrWhiteSpace(str);
    }

    public static void AppendUrlSegment<T>(this RestRequest restRequest, string name, T value)
    {
        ArgumentNullException.ThrowIfNull(value);
        string? valueStr = value.ToString();
        ArgumentException.ThrowIfNullOrWhiteSpace(valueStr);

        StringBuilder uriBuilder = new StringBuilder(restRequest.Resource);
        if (uriBuilder[^1] != '/')
            uriBuilder.Append('/');
        uriBuilder.Append('{').Append(name).Append('}');
        restRequest.Resource = uriBuilder.ToString();
        restRequest.AddUrlSegment(name, valueStr);
    }
}