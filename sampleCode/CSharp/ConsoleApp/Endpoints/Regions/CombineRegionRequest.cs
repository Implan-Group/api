namespace ConsoleApp.Regions;

public class CombineRegionRequest
{
    /// <summary>
    /// A unique-per-Project description for this Combined Region
    /// </summary>
    public string Description { get; set; }

    /// <summary>
    /// An array of the HashIds for all the Regions to be combined
    /// </summary>
    public string[] HashIds { get; set; } = [];

    /// <summary>
    /// An array of the Urids for all the Regions to be combined
    /// </summary>
    public long[] Urids { get; set; } = [];
}