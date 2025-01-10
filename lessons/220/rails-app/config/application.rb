require_relative "boot"

require "active_record/railtie"
require "action_controller/railtie"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module MyRails
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 8.0

    # Please, add to the `ignore` list any other `lib` subdirectories that do
    # not contain `.rb` files, or that should not be reloaded or eager loaded.
    # Common ones are `templates`, `generators`, or `middleware`, for example.
    config.autoload_lib(ignore: %w[assets tasks])

    # Configuration for the application, engines, and railties goes here.
    #
    # These settings can be overridden in specific environments using the files
    # in config/environments, which are processed later.
    #
    # config.time_zone = "Central Time (US & Canada)"
    # config.eager_load_paths << Rails.root.join("extras")

    # Only loads a smaller set of middleware suitable for API only apps.
    # Middleware like session, flash, cookies can be added back manually.
    # Skip views, helpers and assets when generating a new resource.
    config.api_only = true
    config.secret_key_base = 'secret'

    config.middleware.delete Rack::Sendfile
    config.middleware.delete ActionDispatch::Static
    config.middleware.delete ActionDispatch::Executor
    config.middleware.delete Rack::Runtime
    config.middleware.delete ActionDispatch::RequestId
    config.middleware.delete ActionDispatch::RemoteIp
    config.middleware.delete Rails::Rack::Logger
    config.middleware.delete ActionDispatch::ShowExceptions
    config.middleware.delete ActionDispatch::DebugExceptions
    config.middleware.delete ActionDispatch::Callbacks
    config.middleware.delete Rack::Head
    config.middleware.delete Rack::ConditionalGet
    config.middleware.delete Rack::ETag

    Oj.default_options = { mode: :compat }
    Oj.optimize_rails
  end
end
