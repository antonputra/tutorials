public class Config(IConfiguration config)
{
    public string? Region = config.GetValue<string>("S3:region");
    public string? User = config.GetValue<string>("S3:user");
    public string? Secret = config.GetValue<string>("S3:secret");
    public string? S3Endpoint = config.GetValue<string>("S3:endpoint");
    public string? S3ImgPath = config.GetValue<string>("S3:imgPath");
    public string? S3Bucket = config.GetValue<string>("S3:bucket");
    public string? DbHost = config.GetValue<string>("Db:host");
    public string? DbUser = config.GetValue<string>("Db:user");
    public string? DbPassword = config.GetValue<string>("Db:password");
    public string? DbDatabase = config.GetValue<string>("Db:database");
}
