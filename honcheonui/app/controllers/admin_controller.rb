class AdminController < ApplicationController
	# GET /admin/user
	def user
		@users = User.search(params[:search]).paginate(
			:page => params[:page], :per_page=>params[:per_page])

		@agent = User.where(:email => 'agent@example.com').first

		respond_to do |format|
			format.html
			format.json { render :json => @users.to_json }
			format.datatables
		end
	end
end
# vim:set ts=4 sw=4:
