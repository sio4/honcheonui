class Server < ActiveRecord::Base
	validates :name,	:presence => true
	validates :uuid,	:presence => true
	validates :uuid,	:uniqueness => true

	has_many :logs
end
