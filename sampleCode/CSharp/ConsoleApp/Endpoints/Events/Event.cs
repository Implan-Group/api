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

/// <summary>
/// The base class for all Events, the properties here are shared with all Impact Event Types
/// </summary>
public record class Event
{
    /// <summary>
    /// The specific Impact Event Type for this event. 
    /// </summary>
    public virtual string ImpactEventType => "Empty";

    /// <summary>
    /// Unique-per-Project description of this Event
    /// </summary>
    public required string Title { get; set; }

    /// <summary>
    /// Unique identifier for this Event
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Unique identifier for the Project this Event belongs to
    /// </summary>
    public Guid ProjectId { get; set; }

    /// <summary>
    /// Additional Tags to associate with this Event
    /// </summary>
    public string[] Tags { get; set; } = [];
}
