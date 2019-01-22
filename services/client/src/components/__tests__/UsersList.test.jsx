import React from 'react';
import {shallow} from 'enzyme';
import renderer from 'react-test-renderer';

import UsersList from '../UsersList';

const users = [
    {
        'active': true,
        'email': 'seed1@mail.com',
        'id': 1,
        'username': 'seed1'
    },
    {
        'active': true,
        'email': 'seed2@mail.org',
        'id': 2,
        'username': 'seed2'
    }
];

test('UsersList renders properly', () => {
    const wrapper = shallow(<UsersList users={users}/>);
    const element = wrapper.find('h4');
    expect(element.length).toBe(2);
    expect(element.get(0).props.children).toBe('seed1');
});

test('UsersList renders a snapshot properly', () => {
    const tree = renderer.create(<UsersList users={users}/>).toJSON();
    expect(tree).toMatchSnapshot();
});