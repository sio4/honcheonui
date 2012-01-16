class TokenManagerController < ApplicationController
	def update
		@user = User.find(params[:id])
		@user.reset_authentication_token!
		redirect_to edit_user_registration_path(@user)
	end
end
