% from string import ascii_lowercase as ALPHA
% from itertools import cycle

% from cleaver.experiment import VariantStat

<html>
<head>
    <style type="text/css">
        body  {
            font-family: sans-serif;
            padding: .5em 1em;
            margin: 0;
        }
        img#logo  {
            margin: 5px 0 25px 0;
        }
        a  {
            color: #62C2D7;
        }
        div.experiment  {
            background: #F5F5F5;
            border: 1px solid #F0F0F0;
            padding: 15px;
            padding-top: 5px;
            border-radius: 10px;
            -moz-border-radius: 10px;
            -webkit-border-radius: 10px;
        }
        div.experiment .head h2  {
            color: #62C2D7;
            line-height: 25%;
        }
        div.experiment .head p.started_on  {
            font-size: 85%;
        }
        div.experiment .results  {
            background: #FFF;
            padding: 15px;
            border-radius: 10px;
            -moz-border-radius: 10px;
            -webkit-border-radius: 10px;
        }
        p.started_on  {
            font-size: 90%;
        }
        table  {
            border-collapse: collapse;
            width: 100%;
        }
        th, td  {
            padding: 8px;
            text-align: center;
        }
        th  {
            background: #F9F9F9;
        }
        td.left  {
            text-align: left;
        }
        th  {
            font-weight: bold;
        }
        td  {
            border-bottom: 1px dotted #DDD;
        }
        tr.last td  {
            border-bottom: 0;
        }
        td span.pill  {
            display: inline-block;
            background: #CCC;
            color: #FFF;
            padding: 5px 8px;
            text-transform: uppercase;
            font-size: 12px;
            font-weight: bold;
            -webkit-border-radius: 16px;
            border-radius: 16px;
        }
        td.rate, span.better  {
            color: #7EA407;
        }
        span.better  {
            font-weight: bold;
        }
        span.better:before  {
            content: '+'
        }
        div.btn  {
            display: inline-block;
            background: #62C2D7;
            color: #FFF;
            padding: 5px 8px;
            text-transform: uppercase;
            font-size: 12px;
            font-weight: bold;
            -webkit-border-radius: 5px;
            border-radius: 5px;
        }
    </style>
</head>
<body>

    <img id="logo" src="data:;base64,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" />

    % for e in backend.all_experiments():
        <div class="experiment">

            <div class="head">
                <h2>{{e.name}}</h2>

                <p class="started_on">
                    Started
                    {{e.started_on.strftime('%a, %b %d, %Y').replace(' 0', ' ')}}
                </p>
            </div>

            <div class="results">
                <table>
                    <tr>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th>Participants</th>
                        <th>Conversions</th>
                        <th>Conversion Rate</th>
                        <th>Improvement from Control</th>
                        <th></th>
                    </tr>
                    % colors = cycle(('#62C2D7', '#7EA407', '#E3690E'))
                    % for i, v in enumerate(e.variants):
                        % s = VariantStat(v, e)
                        % cc = VariantStat(e.control, e).conversion_rate
                        <tr>
                            % if i == 0:
                                <td class="left"><b>Control</b></td>
                                <td class="left">
                                    <span class="pill control">X</span>
                                </td>
                            % else:
                                <td class="left"><b>Variant</b></td>
                                <td class="left">
                                    <span class="pill" style="background:{{colors.next()}};">
                                        {{ALPHA[i-1].upper()}}
                                    </span>
                                </td>
                            % end
                            <td class="left">{{v}}</td>
                            <td>{{e.participants_for(v) or '-'}}</td>
                            <td>{{e.conversions_for(v) or '-'}}</td>
                            <td class="rate">
                                {{percentage(s.conversion_rate)}}
                            </td>
                            <td>
                                % if v != e.control and cc > 0:
                                    % if s.conversion_rate > cc:
                                        <span class="better">
                                            {{percentage(abs((s.conversion_rate/cc) - 1))}}
                                        </span>
                                    % else:
                                        - 
                                    % end
                                % elif v == e.control:
                                    N/A
                                % elif cc == 0:
                                    -
                                % end
                            </td>
                            <td class="left">
                                % if s.z_score != 'N/A' and s.conversion_rate > cc:
                                    <a href="#" title="Z-Score: {{s.z_score}}">{{s.confidence_level}}</a>
                                % end
                            </td>
                        </tr>
                    % end
                    <tr class="last">
                        <td class="left"><b>Total</b></td>
                        <td />
                        <td />
                        <td>{{e.participants or '-'}}</td>
                        <td>{{e.conversions or '-'}}</td>
                        <td />
                        <td />
                        <td />
                    </tr>
                </table>
            </div>
        </div>
    % end

</body>
</html>
