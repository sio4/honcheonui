class HomeController < ApplicationController
  def index
    # for tab auto-loading, registered menu.
    menu = {
      "servers" => {:label=>"All Servers", :url=>"/servers"},
      "wiki" => {:label=>"Wiki", :url=>"/wikis"},
    }
    if params[:tab]:
      key = params[:tab]
    else
      key = "servers"
    end
    @tab_id = menu[key][:label].gsub(/ /, "_").downcase
    @tab_label = menu[key][:label]
    @tab_url = menu[key][:url]
  end

end

# vim:set ts=2 sw=2 expandtab:
