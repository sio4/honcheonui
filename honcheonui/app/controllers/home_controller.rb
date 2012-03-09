class HomeController < ApplicationController
  def index
    # for tab auto-loading,
    # registered menu. :id must equal to key.
    menu = {
      "servers" => {:id=>"servers", :name=>"All Servers", :url=>"/servers"},
      "wiki" => {:id=>"wiki", :name=>"Wiki", :url=>"/wikis"},
    }
    if params[:tab]:
      key = params[:tab]
    else
      key = "servers"
    end
    @tab_id = menu[key][:id]
    @tab_name = menu[key][:name]
    @tab_url = menu[key][:url]
  end

end

# vim:set ts=2 sw=2 expandtab:
