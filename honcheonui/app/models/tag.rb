class Tag < ActiveRecord::Base
	validates :name,	:presence => true

	has_many :taglinks
	has_many :servers, :through => :taglinks,
		:source => :star, :source_type => 'Server'

	### for jstree tookit, used in side menu server tree.
	def as_json(options={})
		data = {
			:data => self.name + " (" + self.category + ")",
			:attr => {
				:id => 'list-' + self.name,
				:title => 'server ' + self.category.to_s + '...',
				:rel => 'tag',
			},
			:state => 'closed',
			:metadata => {:description => self.description},
		}
		data[:children] = children = []
		self.servers.each do |s|
			style = s.confirmed ? '' : 'font-style:italic'
			icon = '/images/icons/os-' + s.os_id[0..5].to_s.downcase + '-16.png'
			children << {
				:data => {
					:title => s.name,
					:icon => icon,
					:attr => {:style => style},
				},
				:attr => {:style => style, :rel => 'server'},
				:metadata => {
					:id => s.id,
					:name => s.name,
					:description => s.desc,
					:confirmed => s.confirmed,
					:automated => s.st_automation,
					:monitered => s.st_monitoring
				}
			}
		end
		return data
	end
end
# vim:set ts=4 sw=4:
