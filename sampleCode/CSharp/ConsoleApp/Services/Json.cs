using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

namespace ConsoleApp.Services;

public static class Json
{
    internal static readonly JsonSerializerOptions JsonSerializerOptions = new JsonSerializerOptions()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
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

    public static string Serialize<T>(T value)
    {
        return JsonSerializer.Serialize(value, JsonSerializerOptions);
    }

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