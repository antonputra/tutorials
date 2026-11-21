using Amazon;
using Amazon.Runtime;
using Amazon.S3;
using Amazon.S3.Model;

namespace cs_app_aot;

public sealed class AmazonS3Uploader
{
    private readonly AmazonS3Client _client;

    public AmazonS3Uploader(string? accessKey, string? secretKey, string? endpoint, string? region)
    {
        var creds = new BasicAWSCredentials(accessKey, secretKey);
        var cfg = new AmazonS3Config
        {
            ForcePathStyle = true
        };

        if (!string.IsNullOrWhiteSpace(endpoint))
            cfg.ServiceURL = endpoint;
        if (!string.IsNullOrWhiteSpace(region))
            cfg.RegionEndpoint = RegionEndpoint.GetBySystemName(region);

        _client = new AmazonS3Client(creds, cfg);
    }

    public Task Upload(string? bucket, string key, string? path, CancellationToken ct = default)
        => _client.PutObjectAsync(new PutObjectRequest { BucketName = bucket, Key = key, FilePath = path }, ct);
}