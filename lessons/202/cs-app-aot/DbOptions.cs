namespace cs_app;

internal sealed class DbOptions
{
    public const string PATH = "Db";

    public string Host { get; set; } = string.Empty;
    public string User { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string Database { get; set; } = string.Empty;
}
