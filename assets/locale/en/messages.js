/* eslint-disable */module.exports={languageData:{"plurals":function(n,ord){var s=String(n).split("."),v0=!s[1],t0=Number(s[0])==n,n10=t0&&s[0].slice(-1),n100=t0&&s[0].slice(-2);if(ord)return n10==1&&n100!=11?"one":n10==2&&n100!=12?"two":n10==3&&n100!=13?"few":"other";return n==1&&v0?"one":"other"}},messages:{"locales.el":"Greek","locales.en":"English","selectedRow.numberOfRows":function(a){return[a("0","plural",{0:"No rows selected",one:["#"," row selected"],other:["#"," rows selected"]})]},"workflow.visibility.private":"Private","workflow.visibility.public":"Public","workflows.navbar.training":"TRAINING","workflows.navbar.workflows":"WORKFLOWS","accounts.sign_up.fields.first_name.placeholder":"First name","accounts.sign_up.fields.last_name.placeholder":"Last name","py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.shouldBeText":function(a){return[a("columns","plural",{offset:2,1:["The column ",a("0")," must be converted to Text."],2:["The columns ",a("0")," and ",a("1")," must be converted to Text."],one:["The columns ",a("0"),", ",a("1")," and ",a("2")," must be converted to Text."],other:["The columns ",a("0"),", ",a("1")," and ","#"," others must be converted to Text."]})]},"py.renderer.execute.types.PromptingError.WrongColumnType.as_error_message.general":function(a){return[a("columns","plural",{offset:2,1:["The column ",a("0")," must be converted from ",a("found_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""})," to ",a("best_wanted_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""}),"."],2:["The columns ",a("0")," and ",a("1")," must be converted from ",a("found_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""})," to ",a("best_wanted_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""}),"."],one:["The columns ",a("0"),", ",a("1")," and ",a("2")," must be converted from ",a("found_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""})," to ",a("best_wanted_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""}),"."],other:["The columns ",a("0"),", ",a("1")," and ","#"," others must be converted from ",a("found_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""})," to ",a("best_wanted_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""}),"."]})]},"py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.shouldBeText":"Convert to Text.","py.renderer.execute.types.PromptingError.WrongColumnType.as_quick_fix.general":function(a){return["Convert ",a("found_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""})," to ",a("best_wanted_type","select",{text:"Text",number:"Numbers",datetime:"Dates & Times",other:""}),"."]},"py.renderer.execute.wf_module.wrap_render_errors":function(a){return["Something unexpected happened. We have been notified and are working to fix it. If this persists, contact us. Error code: ",a("error_code")]},"py.renderer.execute.wf_module._render_module.TabCycleError":"The chosen tab depends on this one. Please choose another tab.","py.renderer.execute.wf_module._render_module.TabOutputUnreachableError":"The chosen tab has no output. Please select another one.","py.renderer.execute.wf_module._render_module.noLoadedModule":"Please delete this step: an administrator uninstalled its code.","accounts.sign_in.title":"Sign in","accounts.sign_in.forgot_password_prompt":"Forgot Password?","accounts.sign_in.button":"Sign In","accounts.sign_up.title":"Sign Up","accounts.sign_up.login_prompt":"If you have already created an account, then please <a0>log in</a0>.","accounts.emails.password_reset.subject":"Password Reset E-mail","notifications.new_data_version.subject":function(a){return["New data available in ",a("workflow_name")]}}};