/** @jsx React.DOM */
angular.module('cyb.varer').factory('SalgsvarerIndexListView', function ($compile, $filter, PrisDato, PrisMargin) {
    return React.createClass({
        render: function () {
            return (
                <table className="table table-striped table-condensed">
                    <thead>
                        <tr>
                            <th>Navn</th>
                            <th>Status</th>
                            <th>Kasse#</th>
                            <th>Intern</th>
                            <th>Ekstern</th>
                            <th>Råvarer (priser eks mva)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.props.items.map(function (item) {
                            return (
                                <tr key={item.id}>
                                    <td>
                                        {item.kategori ? item.kategori + ': ' : ''}
                                        {/*<a ui-sref="salgsvare({id:item.id})">{item.navn}</a>*/}
                                        <a href={'admin/varer/salgsvare/' + item.id + '/'} target="_self">{item.navn}</a>
                                        <br/>
                                        <a className="gruppe-link" href={'admin/kontoer/'+item.salgskonto.id} title={item.salgskonto.navn}>{item.salgskonto.navn}</a>
                                    </td>
                                    <td>{item.status}</td>
                                    <td>{item.kassenr}</td>
                                    <td>
                                        {item.salgspris.pris_intern ?
                                            <span>
                                                {$filter('price')(item.salgspris.pris_intern, 0)}
                                                {item.innpris ?
                                                    <span>
                                                        <br/>
                                                        <PrisMargin innPris={item.innpris} utPris={item.salgspris.pris_intern} utMva={item.salgspris.mva} />
                                                    </span> : ''}
                                            </span> : 'Se ekstern'}
                                    </td>
                                    <td>
                                        {item.salgspris.pris_ekstern ?
                                            <span>
                                                {$filter('price')(item.salgspris.pris_ekstern, 0)}
                                                {item.innpris ?
                                                    <span>
                                                        <br/>
                                                        <PrisMargin innPris={item.innpris} utPris={item.salgspris.pris_ekstern} utMva={item.salgspris.mva} />
                                                    </span> : ''}
                                            </span> : 'Ikke salg'}
                                    </td>
                                    <td>
                                        <ul>
                                            {item.raavarer.map(function (meta) {
                                                return (
                                                    <li key={meta.id}>
                                                        {/*<span ng-show="::meta.raavare.kategori">{meta.raavare.kategori}: </span>*/}
                                                        {/*<span ng-if="meta.mengde == meta.raavare.mengde">1 stk</span>*/}
                                                        {meta.mengde != meta.raavare.mengde ? meta.mengde + ' ' + meta.raavare.enhet + ' ' : ''}
                                                        <a href={'varer/råvarer/'+meta.raavare.id}>{meta.raavare.navn}</a>

                                                        {meta.innpris ? <span>
                                                            &nbsp;({$filter('price')(meta.innpris_accurate, 2)} <PrisDato dato={meta.innpris.dato} />)
                                                        </span> : ''}
                                                    </li>);
                                            })}
                                        </ul>
                                    </td>
                                </tr>);
                            })}
                    </tbody>
                </table>
            );
        }
    });
});