class Server < ActiveRecord::Base
	validates :name,	:presence => true
	validates :uuid,	:presence => true
	validates :uuid,	:uniqueness => true

	has_many :stats
	has_many :logs

	has_many :taglinks, :as => :star
	has_many :tags, :through => :taglinks
end
