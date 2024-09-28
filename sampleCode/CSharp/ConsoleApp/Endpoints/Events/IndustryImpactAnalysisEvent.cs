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

public sealed record class IndustryImpactAnalysisEvent : Event
{
    public required int IndustryCode { get; set; }
    public double? IntermediateInputs { get; set; }
    public double? TotalEmployment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public double? WageAndSalaryEmployment { get; set; }
    public double? ProprietorEmployment { get; set; }
    public double? TotalLaborIncome { get; set; }
    public double? OtherPropertyIncome { get; set; }
    public double? TaxOnProductionAndImports { get; set; }
    public double? LocalPurchasePercentage { get; set; } = 1.0;
    public double? TotalOutput { get; set; }
    public bool IsSam { get; set; }
    public int? SpendingPatternDatasetId { get; set; }
    public SpendingPatternValueType SpendingPatternValueType { get; set; }
    public SpendingPatternCommodity[] SpendingPatternCommodities { get; set; } = [];

    public override string ImpactEventType => "IndustryImpactAnalysis";
}
