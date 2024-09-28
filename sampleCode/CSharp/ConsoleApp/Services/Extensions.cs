using System.Diagnostics.CodeAnalysis;
using System.Runtime.CompilerServices;

namespace ConsoleApp.Services;

/*
# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

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
