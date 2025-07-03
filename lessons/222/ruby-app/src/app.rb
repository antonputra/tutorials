# frozen_string_literal: true

require_relative 'device'

class App
  def call(env)
    case env['PATH_INFO']

    when '/api/devices'
      if env['REQUEST_METHOD'] == 'GET'
        response(Device.list, 200)
      else
        begin
          device = Device.create(Oj.load(env['rack.input'].read))

          response(device.to_h, 201)
        rescue StandardError => e
          response({ 'message' => e.message }, 400)
        end
      end

    when '/up'
      response({ 'message' => 'OK' }, 200)
      
    else
      response({ 'message' => 'Not Found' }, 404)
    end
    
  end

  def response(data, status)
    [status, { 'Content-Type' => 'application/json' }, [Oj.dump(data)]]
  end
end
