class Server < ActiveRecord::Base
	validates :name,	:presence => true
end
