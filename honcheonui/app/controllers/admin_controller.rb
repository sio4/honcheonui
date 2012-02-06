class AdminController < ApplicationController
	# GET /admin/user
	# GET /admin/user.json
	def user
		@users = User.all
		@meta = {:total => @users.length}

		respond_to do |format|
			format.html
			format.json { render :json => {:meta => @meta, :objs => @users } }
		end
	end
end
# vim:set ts=4 sw=4:
