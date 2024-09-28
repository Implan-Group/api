namespace ConsoleApp.Endpoints.Events;

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

public sealed record class IndustryOutputEvent : Event
{
    public override string ImpactEventType => "IndustryOutput";

    /// <summary>
    /// Total output value of this Industry Output Event
    /// </summary>
    public required double? Output { get; set; }

    /// <summary>
    /// Total employment value
    /// </summary>
    public double? Employment { get; set; }

    /// <summary>
    /// Total employee compensation
    /// </summary>
    public double? EmployeeCompensation { get; set; }

    /// <summary>
    /// Total proprietor compensation
    /// </summary>
    public double? ProprietorIncome { get; set; }

    /// <summary>
    /// The Industry's Code (see <see cref="IndustryCodeEndpoints"/>)
    /// </summary>
    public int IndustryCode { get; set; }

    /// <summary>
    ///  The Dataset Id (see <see cref="DataSetEndpoints"/>)
    /// </summary>
    public int? DatasetId { get; set; }

    public MarginType? MarginType { get; set; }
    public double? Percentage { get; set; }
}
