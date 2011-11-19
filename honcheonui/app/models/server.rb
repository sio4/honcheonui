class Server < ActiveRecord::Base
	validates :name,	:presence => true

	has_many :logs
end
