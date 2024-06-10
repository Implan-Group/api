using System.Diagnostics.CodeAnalysis;
using System.Runtime.CompilerServices;

namespace ConsoleApp.Services;

public static class Extensions
{
    /// <summary>
    /// If <paramref name="value"/> is <c>null</c>, throw an <see cref="ArgumentNullException"/>,
    /// otherwise return it
    /// </summary>
    /// <param name="value">The value to check for <c>null</c></param>
    /// <param name="valueName">The captured name of the variable to use for errors</param>
    /// <typeparam name="T">The generic <see cref="Type"/> of the <paramref name="value"/> parameter</typeparam>
    /// <returns>The non-<c>null</c> <paramref name="value"/></returns>
    /// <exception cref="ArgumentNullException">Thrown if <paramref name="value"/> is <c>null</c></exception>
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

    /// <summary>
    /// Is this <see cref="string"/> <c>null</c>, empty (length = 0), or composed entirely of whitespace characters?
    /// </summary>
    /// <param name="str">The <see cref="string"/> to check</param>
    /// <returns>
    /// <c>true</c> if the <see cref="string"/> is <c>null</c>, empty, or whitespace
    /// <c>false</c> if it is not
    /// </returns>
    public static bool IsNullOrWhiteSpace([NotNullWhen(false)] this string? str)
    {
        return string.IsNullOrWhiteSpace(str);
    }
}