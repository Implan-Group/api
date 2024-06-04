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
}