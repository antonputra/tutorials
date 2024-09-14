const std = @import("std");
const zap = @import("zap");

const Device = struct {
    id: ?c_int = null,
    mac: ?[]const u8 = null,
    firmware: ?[]const u8 = null,
};

fn on_request(r: zap.Request) void {
    if (r.methodAsEnum() != .GET) return;

    if (r.path) |the_path| {
        if (std.mem.startsWith(u8, the_path, "/healthz")) {
            r.sendBody("OK") catch return;
        }
    }

    if (r.path) |the_path| {
        if (std.mem.startsWith(u8, the_path, "/api/devices")) {
            const devs = [_]Device{Device{ .id = 1, .mac = "EF-2B-C4-F5-D6-34", .firmware = "2.1.5" }};

            var buf: [100]u8 = undefined;
            var json_to_send: []const u8 = undefined;

            if (zap.stringifyBuf(&buf, devs, .{})) |json| {
                json_to_send = json;
            } else {
                json_to_send = "error";
            }

            r.sendJson(json_to_send) catch return;
        }
    }
}

pub fn main() !void {
    var listener = zap.HttpListener.init(.{
        .port = 8080,
        .on_request = on_request,
        .log = false,
    });
    try listener.listen();

    std.debug.print("Listening on 0.0.0.0:{d}\n", .{8080});

    zap.start(.{
        .threads = 2,
        .workers = 1,
    });
}
