using System.Net;

namespace ConsoleApp.Models;

public sealed record class ActionResult
{
    public string Type { get; set; }
    public string Title { get; set; }
    public HttpStatusCode Status { get; set; }
    public string Detail { get; set; }
    public string TraceId { get; set; }
}

public sealed record class ErrorMessage
{
    public string Message { get; set; }
}