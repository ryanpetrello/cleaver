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
        h1  {
            margin-bottom: 35px;
            display: inline-block;
            background: #A6CD09;
            color: #FFF;
            padding: 5px 8px;
            padding-right: 3px;
            text-transform: uppercase;
            font-size: 18px;
            -webkit-border-radius: 5px 0px 0px 5px;
            border-radius: 5px 0px 0px 5px;
        }
        h1.ver  {
            background: #62C2D7;
            border-left: 1px solid #52B2C7;
            color: #FFF;
            padding-left: 3px;
            padding-right: 8px;
            -webkit-border-radius: 0px 5px 5px 0px;
            border-radius: 0px 5px 5px 0px;
        }
        h1 span.sub  {
            font-size: 12px;
            font-weight: normal;
            text-transform: none;
            color: #000;
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

    <h1>Clea</h1><h1 class="ver">ver</h1>

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
