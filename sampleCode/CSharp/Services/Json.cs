namespace Implan.ApiSamples.Services;

/// <summary>
/// The JSON settings every request and response uses.
/// </summary>
/// <remarks>
/// The Impact API speaks <c>camelCase</c>; C# is written in <c>PascalCase</c>. The
/// naming policy below does that conversion, so the models are plain C# types with
/// no attribute on every property.
///
/// Two settings matter beyond the naming.
///
/// Unknown properties are ignored rather than rejected, which is the default and is
/// worth keeping: the API gains fields over time, and a model that threw on an
/// unexpected key would turn a routine addition into a broken sample. Models that
/// want to see those extras declare a <c>[JsonExtensionData]</c> dictionary.
///
/// Nulls are left out when writing. The API reads an absent optional field as "not
/// supplied", which is what a null means in these models: a Group carries exactly
/// one region identifier and the other three stay absent.
/// </remarks>
public static class Json
{
    public static readonly JsonSerializerOptions Options = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        WriteIndented = false,
        Converters =
        {
            // Enums travel as their names, for example "IndustryOutput" and
            // "ProducerPrice", not as numbers.
            new JsonStringEnumConverter(),
        },
    };

    /// <summary>The same settings, formatted for a human to read.</summary>
    public static readonly JsonSerializerOptions PrettyOptions = new(Options)
    {
        WriteIndented = true,
    };

    /// <summary>Serializes a value the way the API expects to receive it.</summary>
    public static string Serialize<T>(T value) => JsonSerializer.Serialize(value, Options);

    /// <summary>Deserializes a JSON document into a model.</summary>
    public static T? Deserialize<T>(string json) => JsonSerializer.Deserialize<T>(json, Options);
}
