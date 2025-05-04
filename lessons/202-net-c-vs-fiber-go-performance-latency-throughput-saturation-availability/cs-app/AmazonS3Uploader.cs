using Amazon.S3;
using Amazon.S3.Model;
using Amazon.Runtime;

public class AmazonS3Uploader
{
    private readonly AmazonS3Client client;

    public AmazonS3Uploader(string? accessKey, string? secretKey, string? endpoint)
    {
        var credentials = new BasicAWSCredentials(accessKey, secretKey);
        var clientConfig = new AmazonS3Config()
        {
            ServiceURL = endpoint,
            ForcePathStyle = true,
        };

        client = new AmazonS3Client(credentials, clientConfig);
    }

    public async Task Upload(string? bucket, string key, string? path)
    {
        try
        {
            PutObjectRequest putRequest = new PutObjectRequest
            {
                BucketName = bucket,
                Key = key,
                FilePath = path
            };

            PutObjectResponse response = await client.PutObjectAsync(putRequest);
        }
        catch (AmazonS3Exception amazonS3Exception)
        {
            if (amazonS3Exception.ErrorCode != null &&
                (amazonS3Exception.ErrorCode.Equals("InvalidAccessKeyId")
                ||
                amazonS3Exception.ErrorCode.Equals("InvalidSecurity")))
            {
                throw new Exception("Check the provided AWS Credentials.");
            }
            else
            {
                throw new Exception("Error occurred: " + amazonS3Exception.Message);
            }
        }
    }
}
