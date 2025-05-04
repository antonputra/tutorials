public class Image(string key)
{
    public Guid ImageUuid = Guid.NewGuid();
    public DateTime CreatedAt = DateTime.Now;
    public string ObjKey = key;
}