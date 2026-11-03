namespace Implan.ApiSamples.Services;

/// <summary>
/// Reading comma-separated text, shared by the bulk workflow's input files and the
/// API's CSV reports.
/// </summary>
public static class Csv
{
    /// <summary>Splits one CSV line, honoring double quotes around a field.</summary>
    public static List<string> SplitLine(string line)
    {
        var fields = new List<string>();
        var current = new System.Text.StringBuilder();
        var inQuotes = false;

        foreach (var character in line)
        {
            switch (character)
            {
                case '"':
                    inQuotes = !inQuotes;
                    break;
                case ',' when !inQuotes:
                    fields.Add(current.ToString().Trim());
                    current.Clear();
                    break;
                default:
                    current.Append(character);
                    break;
            }
        }

        fields.Add(current.ToString().Trim());
        return fields;
    }
}
