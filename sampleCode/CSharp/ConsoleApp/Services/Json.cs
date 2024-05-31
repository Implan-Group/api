using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

namespace ConsoleApp.Services;

public static class Json
{
    internal static readonly JsonSerializerOptions JsonSerializerOptions = new JsonSerializerOptions()
    {
        // Convert our Model Properties to CamelCase
        // e.g.: "Name" -> "name", "ThingId" -> "thingId"
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false,
        Converters =
        {
            // Configure Enums
            new JsonStringEnumConverter(
                // CamelCase the enum name (same as PropertyNamingPolicy)
                namingPolicy: JsonNamingPolicy.CamelCase, 
                // Allow integer values as inputs
                allowIntegerValues: true),
        },
        
        // TODO: Remove all below after debugging
        //UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow, 
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
        {
            Modifiers =
            {
                ThrowNullAssignedToNonNull,
            }
        }
    };

    /// <summary>
    /// Serialize the given <paramref name="value"/>
    /// </summary>
    /// <param name="value"></param>
    /// <typeparam name="T"></typeparam>
    /// <returns>
    /// A json <see cref="string"/> serialization
    /// </returns>
    public static string Serialize<T>(T value)
    {
        return JsonSerializer.Serialize(value, JsonSerializerOptions);
    }

    /// <summary>
    /// Deserialize the given json <see cref="string"/> into a <typeparamref name="T"/>
    /// </summary>
    /// <param name="json"></param>
    /// <typeparam name="T"></typeparam>
    /// <returns>
    /// A <typeparamref name="T"/> deserialization
    /// </returns>
    public static T? Deserialize<T>(string? json)
    {
        if (json is null) return default;
        return JsonSerializer.Deserialize<T>(json, JsonSerializerOptions);
    }
    
    
    // TODO: Remove all below after debugging
    
    
    private static readonly NullabilityInfoContext _nullabilityInfoContext = new();
    
    private static void ThrowNullAssignedToNonNull(JsonTypeInfo jsonTypeInfo)
    {
        if (jsonTypeInfo.Kind != JsonTypeInfoKind.Object) return;
        foreach (var property in jsonTypeInfo.Properties)
        {
            if (!property.PropertyType.IsValueType &&
                property.Set is not null &&
                property.AttributeProvider is PropertyInfo propertyInfo)
            {
                var nullabilityInfo = _nullabilityInfoContext.Create(propertyInfo);
                if (nullabilityInfo.WriteState != NullabilityState.NotNull)
                    continue;
                // Override the setter to include a null check
                var setter = property.Set;
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