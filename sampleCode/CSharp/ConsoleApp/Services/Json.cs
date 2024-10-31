using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

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

/// <summary>
/// Contains all the configuration information for the standard `json` formatting
/// </summary>
public static class Json
{
    /// <summary>
    /// The configured Json serialization options
    /// </summary>
    internal static readonly JsonSerializerOptions JsonSerializerOptions = new JsonSerializerOptions()
    {
        // Convert our Model Properties to CamelCase
        // e.g.: "Name" -> "name", "ThingId" -> "thingId"
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        // Add newlines and indents to the output to make it more readable
        WriteIndented = true,
        // Allow trailing commas
        AllowTrailingCommas = true,
        Converters =
        {
            // Configure Enums
            new JsonStringEnumConverter(
                // CamelCase the enum name (same as PropertyNamingPolicy)
                namingPolicy: JsonNamingPolicy.CamelCase, 
                // Allow integer values as inputs
                allowIntegerValues: true),
        },
        
        // These lines below are for debugging
        // UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow, 
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
        {
            Modifiers =
            {
                ThrowNullAssignedToNonNull,
            }
        }
    };

    /// <summary>
    /// Serialize the given <paramref name="value"/> using the standard Json serializer
    /// </summary>
    /// <param name="value">The value to serialize</param>
    /// <typeparam name="T">The generic <see cref="Type"/> of the <paramref name="value"/></typeparam>
    /// <returns>
    /// A json-<see cref="string"/> serialization of <paramref name="value"/>
    /// </returns>
    public static string Serialize<T>(T value)
    {
        return JsonSerializer.Serialize(value, JsonSerializerOptions);
    }

    /// <summary>
    /// Deserialize the given json <see cref="string"/> into a <typeparamref name="T"/>
    /// </summary>
    /// <param name="json">The json-<see cref="string"/> to deserialize</param>
    /// <typeparam name="T">The generic <see cref="Type"/> to deserialize to</typeparam>
    /// <returns>
    /// A <typeparamref name="T"/> deserialization of the json string
    /// </returns>
    public static T? Deserialize<T>(string? json)
    {
        if (json is null) return default;
        return JsonSerializer.Deserialize<T>(json, JsonSerializerOptions);
    }
    
    
    /*   The below code is only included for Debugging   */
    
    private static readonly NullabilityInfoContext _nullabilityInfoContext = new();
    
    private static void ThrowNullAssignedToNonNull(JsonTypeInfo jsonTypeInfo)
    {
        if (jsonTypeInfo.Kind != JsonTypeInfoKind.Object) return;
        foreach (JsonPropertyInfo property in jsonTypeInfo.Properties)
        {
            if (!property.PropertyType.IsValueType &&
                property.Set is not null &&
                property.AttributeProvider is PropertyInfo propertyInfo)
            {
                NullabilityInfo nullabilityInfo = _nullabilityInfoContext.Create(propertyInfo);
                if (nullabilityInfo.WriteState != NullabilityState.NotNull)
                    continue;
                // Override the setter to include a null check
                Action<object, object?>? setter = property.Set;
                property.Set = (instance, value) =>
                {
                    if (value is null)
                    {
                        throw new ArgumentNullException(nameof(value),
                            $"Cannot set {propertyInfo.DeclaringType?.Name}.{propertyInfo.Name} to null!");
                    }
                    setter(instance, value);
                };
            }
        }
    }
}
