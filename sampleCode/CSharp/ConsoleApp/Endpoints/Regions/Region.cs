namespace ConsoleApp.Regions;

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

public sealed record class Region
{
    /// <summary>
    /// The HashId for this Region (used to reference this exact Region)
    /// </summary>
    public string HashId { get; set; }

    /// <summary>
    /// The URID for this Region (depreciated way to reference this exact Region)
    /// </summary>
    public long? Urid { get; set; }

    /// <summary>
    /// The User's Model Id for this Region, filled in for Combined and Customized Regions
    /// </summary>
    public int? UserModelId { get; set; }

    /// <summary>
    /// The description of this Region
    /// </summary>
    public string Description { get; set; }

    /// <summary>
    /// Unique identifier for a particular model, used internally
    /// </summary>
    public int? ModelId { get; set; }

    /// <summary>
    /// The current status of the Model's Build progress. Certain complex Models may take time to process until they are `Complete`
    /// </summary>
    public string ModelBuildStatus { get; set; }

    /// <summary>
    /// Total employment value for this Region
    /// </summary>
    public double? Employment { get; set; }

    /// <summary>
    /// Total industry output value for this Region
    /// </summary>
    public double? Output { get; set; }

    /// <summary>
    /// Total value-added for this Region
    /// </summary>
    public double? ValueAdded { get; set; }

    /// <summary>
    /// The Aggregation Scheme that includes this Region
    /// </summary>
    public int AggregationSchemeId { get; set; }

    /// <summary>
    /// The Dataset that includes this Region
    /// </summary>
    public int DatasetId { get; set; }

    /// <summary>
    /// A description of the Dataset that usually includes the Data Year
    /// </summary>
    public string DatasetDescription { get; set; }

    /// <summary>
    /// The Federal Information Processing Standards (FIPS) Code for this Region
    /// </summary>
    public string? FipsCode { get; set; }

    /// <summary>
    /// If a Canadian Region, the Code for the Province
    /// </summary>
    public string? ProvinceCode { get; set; }

    /// <summary>
    /// The M49 standard Code for this Region
    /// </summary>
    public string? M49Code { get; set; }

    /// <summary>
    /// The Region's Type, one of:
    /// `country`, `state`, `msa`, `county`, `Congressional District`, `zipcode`
    /// </summary>
    public string RegionType { get; set; }

    /// <summary>
    /// Whether or not this Region has other children Regions associated with it
    /// e.g. A `state` has many `county` and `zipcode` children
    /// </summary>
    public bool HasAccessibleChildren { get; set; }

    /// <summary>
    /// A further description of the <see cref="RegionType"/>
    /// </summary>
    public string RegionTypeDescription { get; set; }

    /// <summary>
    /// The first non-`null` value among <see cref="ProvinceCode"/>, <see cref="FipsCode"/>, or <see cref="M49Code"/> (in that order) (used internally)
    /// </summary>
    public string? GeoId { get; set; }

    /// <summary>
    /// Whether or not the Region supports Multi-Region Input/Ouput  (MRIO) Analysis
    /// </summary>
    public bool IsMrioAllowed { get; set; }
}
