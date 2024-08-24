namespace cs_app;

internal sealed class S3Options
{
    public const string PATH = "S3";

    public string Region { get; set; } = string.Empty;
    public string Bucket { get; set; } = string.Empty;
    public string Endpoint { get; set; } = string.Empty;
    public bool PathStyle { get; set; }
    public string User { get; set; } = string.Empty;
    public string Secret { get; set; } = string.Empty;
    public string ImgPath { get; set; } = string.Empty;
}
